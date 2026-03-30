# Third-Party Dependency Major Version Upgrades

When `composer.json` constraints widen to include a new major version of ANY dependency
(not just TYPO3 core), the upgrade requires systematic API compatibility validation.

## When This Applies

- `composer.json` changes from `"vendor/package": "^3.0"` to `"^3.0 || ^4.0"`
- A dependency releases a new major version with breaking changes
- Multi-version support is required (e.g., intervention/image v3 + v4)

## Workflow: Third-Party Dependency Upgrade

### Step 1: Enumerate All Usages

Search the entire codebase for ALL usages of the dependency's API:

```bash
# Find all imports/use statements for the package namespace
grep -rn "use Vendor\\Package\\" Classes/ Tests/

# Find all method calls on objects of that type
grep -rn "->methodName(" Classes/

# Find all static calls
grep -rn "Vendor\\Package\\ClassName::" Classes/
```

### Step 2: Cross-Reference Against New Version's API

For each usage found, verify the method/class still exists in the new major version:

1. **Check the package's UPGRADE.md or CHANGELOG** for breaking changes
2. **Read the interface definitions** in both versions — interfaces are the contract
3. **Compare method signatures** (parameter types, return types, parameter order)
4. **Check for renamed/removed classes** (namespace changes are common in major bumps)

### Step 3: Flag Interface vs Concrete Class Methods

**Critical pitfall**: Methods called on interface-typed variables must exist on the
interface in ALL supported versions, not just on the concrete class.

```php
// WRONG: toWebp() exists on ImageInterface in v3 but NOT in v4
public function process(ImageInterface $image): ImageInterface
{
    return $image->toWebp()->save($path);  // Breaks on v4
}

// RIGHT: save() accepts format parameter in v4, use version-safe API
public function process(ImageInterface $image): ImageInterface
{
    return $image->save($path);  // Works on both v3 and v4
}
```

**Validation rule**: For every `->method()` call, check:
- Is the variable typed to an interface or a concrete class?
- Does the method exist on the **interface** (not just the concrete implementation)?
- Does the method exist on the interface in **ALL supported major versions**?

### Step 4: Adapter Pattern for Incompatible APIs

When method signatures differ between major versions, use an adapter:

```php
// Adapter interface (your code)
interface ImageProcessorInterface
{
    public function convertToWebp(object $image, string $path): void;
}

// v3 adapter
class ImageProcessorV3 implements ImageProcessorInterface
{
    public function convertToWebp(object $image, string $path): void
    {
        $image->toWebp()->save($path);
    }
}

// v4 adapter
class ImageProcessorV4 implements ImageProcessorInterface
{
    public function convertToWebp(object $image, string $path): void
    {
        $image->save($path);  // v4 handles format via file extension
    }
}

// Factory selects adapter based on installed version
class ImageProcessorFactory
{
    public static function create(): ImageProcessorInterface
    {
        if (method_exists(ImageInterface::class, 'toWebp')) {
            return new ImageProcessorV3();
        }
        return new ImageProcessorV4();
    }
}
```

### Step 5: Version Detection Pitfalls

**Do NOT use `method_exists()` directly in business logic** — PHPStan narrows the
type and can cause false positives/negatives:

```php
// WRONG: PHPStan narrows $image type after method_exists()
if (method_exists($image, 'toWebp')) {
    $image->toWebp()->save($path);  // PHPStan may still error
} else {
    $image->save($path);
}

// RIGHT: Use adapter pattern with `object` type parameter
// or check on the class/interface name, not the instance:
if (method_exists(ImageInterface::class, 'toWebp')) {
    // v3 path
} else {
    // v4 path
}
```

## PHPStan Multi-Version Validation

### Problem

PHPStan analyzes code against ONE version of installed dependencies at a time.
When you support `^3.0 || ^4.0`, PHPStan with v4 installed will flag v3-only
method calls, and vice versa.

### Solution: Run PHPStan Against Each Major Version

```bash
# Test with v3
composer require vendor/package:^3.0 --no-interaction
./vendor/bin/phpstan analyse

# Test with v4
composer require vendor/package:^4.0 --no-interaction
./vendor/bin/phpstan analyse
```

### CI Matrix for Multi-Version Dependencies

```yaml
# .github/workflows/ci.yml
jobs:
  phpstan:
    strategy:
      matrix:
        include:
          - dependency-version: "^3.0"
            label: "vendor/package v3"
          - dependency-version: "^4.0"
            label: "vendor/package v4"
    steps:
      - run: composer require vendor/package:${{ matrix.dependency-version }} --no-interaction
      - run: ./vendor/bin/phpstan analyse
```

### @phpstan-ignore Tags Are Version-Specific

`@phpstan-ignore` annotations suppress errors for ONE version but the suppressed
code may itself be invalid in another version:

```php
// WRONG: Suppresses the error when v4 is installed, but the code
// itself fails at runtime with v4 because toWebp() doesn't exist
/** @phpstan-ignore method.notFound */
$image->toWebp()->save($path);

// RIGHT: Use adapter pattern so no @phpstan-ignore is needed at all
$this->imageProcessor->convertToWebp($image, $path);
```

**Rule**: If you find yourself adding `@phpstan-ignore` for version-conditional
code, refactor to the adapter pattern instead. The ignore tag masks a real
runtime error in one of the supported versions.

## Test Compatibility for Multi-Version Dependencies

### Mock Methods Must Exist on Interfaces

When mocking dependency interfaces, every `->method('foo')` call must reference
a method that exists on the **interface** in ALL supported versions:

```php
// WRONG: toWebp() is not on ImageInterface in v4
$mock = $this->createMock(ImageInterface::class);
$mock->method('toWebp')->willReturn($encodedImage);

// RIGHT: Mock only methods that exist on the interface in all versions
// Or mock your own adapter interface instead
$mock = $this->createMock(ImageProcessorInterface::class);
$mock->method('convertToWebp')->willReturn(null);
```

### Mock Callback Signatures Must Match

When using `willReturnCallback()`, the callback signature must match the
method signature in the version being tested:

```php
// If save() signature changed between v3 and v4:
// v3: save(string $path): self
// v4: save(string $path, string $format = null, int $quality = 90): self

// The mock callback must be compatible with both:
$mock->method('save')->willReturnCallback(
    function (string $path, ...$args) use ($mock) {
        // Handle both signatures via variadic
        return $mock;
    }
);
```

### Maintaining Test Specificity

When refactoring from version-specific APIs (e.g., `->toWebp()->save()`) to
version-agnostic APIs (e.g., `->save()`), assertions must remain equally specific:

```php
// BEFORE: Specific assertion on toWebp() call chain
$mock->expects($this->once())->method('toWebp');
$encodedMock->expects($this->once())->method('save')->with($outputPath);

// AFTER (WRONG): Lost specificity - just asserts save() was called
$mock->expects($this->once())->method('save')->with($outputPath);

// AFTER (RIGHT): Assert the output format/path is correct
$mock->expects($this->once())->method('save')
    ->with(
        $this->callback(fn($path) => str_ends_with($path, '.webp')),
        // Additional assertions on format parameters if applicable
    );
```

## Checklist: Third-Party Dependency Upgrade

- [ ] Identified all usages of dependency API in `Classes/` and `Tests/`
- [ ] Cross-referenced each usage against new version's changelog/upgrade guide
- [ ] Verified all method calls exist on interfaces (not just concrete classes)
- [ ] Used adapter pattern where method signatures differ between versions
- [ ] No `@phpstan-ignore` tags for version-conditional code (use adapters)
- [ ] PHPStan passes with EACH supported major version installed
- [ ] Test mocks only reference methods on interfaces valid in ALL versions
- [ ] CI matrix tests against each supported major version
- [ ] Mock callbacks match method signatures for all supported versions
