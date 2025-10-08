# Contributing to Marstek Venus Integration

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Marstek Venus Home Assistant integration.

## Code of Conduct

Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Home Assistant development environment
- Git
- Basic understanding of Home Assistant integrations

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/marstek-venus-hacs.git
   cd marstek-venus-hacs
   ```

3. Set up Home Assistant development container or local instance
4. Symlink the integration to your Home Assistant config:
   ```bash
   ln -s $(pwd)/custom_components/marstek_venus ~/.homeassistant/custom_components/
   ```

5. Restart Home Assistant

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### 2. Make Changes

- Follow the existing code style
- Add comments where necessary
- Update translations if adding new strings
- Test your changes thoroughly

### 3. Code Style

This project follows:
- [PEP 8](https://www.python.org/dev/peps/pep-0008/) - Python style guide
- [Black](https://black.readthedocs.io/) - Code formatter
- [isort](https://pycqa.github.io/isort/) - Import sorting

Format your code:
```bash
black custom_components/marstek_venus
isort custom_components/marstek_venus
```

### 4. Testing

Test your changes:
- Manually test all affected features
- Test with different device configurations
- Check for errors in Home Assistant logs
- Verify entities appear correctly

### 5. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for multiple devices"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Testing
- `chore:` - Maintenance

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Create a PR on GitHub with:
- Clear title and description
- List of changes
- Screenshots if applicable
- Reference to related issues

## Project Structure

```
custom_components/marstek_venus/
├── __init__.py          # Integration setup
├── api.py              # API client
├── config_flow.py      # Configuration UI
├── const.py            # Constants
├── coordinator.py      # Data coordinator
├── manifest.json       # Integration metadata
├── sensor.py           # Sensor entities
├── select.py           # Select entities
├── switch.py           # Switch entities
├── services.yaml       # Service definitions
├── strings.json        # Base translations
└── translations/       # Language translations
    ├── de.json
    └── en.json
```

## Adding New Features

### Adding a New Sensor

1. Add sensor definition to `sensor.py`:
```python
MarstekVenusSensorEntityDescription(
    key="new_sensor",
    translation_key="new_sensor",
    name="New Sensor",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    value_fn=lambda data: data.get("component", {}).get("value"),
)
```

2. Add translations to `strings.json` and translation files:
```json
{
  "entity": {
    "sensor": {
      "new_sensor": {
        "name": "New Sensor"
      }
    }
  }
}
```

### Adding a New API Method

1. Add method to `api.py`:
```python
async def get_new_data(self) -> dict[str, Any] | None:
    """Get new data from device."""
    return await self._send_command("Component.GetData", {"id": 0})
```

2. Add to data fetch in `coordinator.py` if needed

### Adding Translations

Add translations for all supported languages:
- `strings.json` (base/English)
- `translations/de.json` (German)
- `translations/en.json` (English)

## Testing Guidelines

### Manual Testing Checklist

- [ ] Integration installs successfully
- [ ] Configuration flow works
- [ ] Device is discovered
- [ ] All sensors show correct values
- [ ] Mode changes work correctly
- [ ] Services function properly
- [ ] Error handling works
- [ ] Reconnection after network loss
- [ ] Multiple device support (if applicable)

### Test Cases

Document test cases in your PR:
```
Test: Battery SOC sensor
1. Configure integration
2. Navigate to sensor.marstek_venus_battery_soc
3. Verify value matches device
4. Verify unit is %
5. Verify updates every 30 seconds
```

## Documentation

Update documentation when adding features:
- `README.md` - User-facing documentation
- `CONTRIBUTING.md` - This file
- Code comments - Inline documentation
- `examples/` - Example configurations

## API Documentation Reference

When implementing features, refer to:
- `Api.md` - Marstek API specification
- Test with real device when possible
- Document any deviations or issues

## Common Issues

### Connection Timeouts
- Check UDP port is open
- Verify device IP address
- Test with `nc -u` or similar tool

### Entity Not Updating
- Check coordinator update interval
- Verify API response format
- Check for errors in HA logs

### Translation Not Working
- Verify translation key matches
- Check JSON syntax
- Restart Home Assistant

## Release Process

Maintainers will:
1. Review and merge PRs
2. Update version in `manifest.json`
3. Update `CHANGELOG.md`
4. Create GitHub release
5. Update HACS repository

## Questions?

- Open an issue for bugs
- Start a discussion for feature requests
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Credits

All contributors will be acknowledged in the project README.

Thank you for contributing! 🎉
