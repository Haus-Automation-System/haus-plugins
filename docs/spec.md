# Plugin Specification

### Folder Structure:

Each plugin folder should adhere to the following structure:

```
plugin
 |
 |- plugin.yaml
 |- module_name
 |   |- __init__.py
 |   |- ...other files
```

### Plugin Manifest (`plugin.yaml`/`plugin.yml`)

A YAML file with the following format:
```yaml
metadata:
  name: plugin_symbolic_name
  version: Plugin version           # (e.g. 0.1.0)
  icon: tabler-icon-name
  display-name: Display Name

run:
  module: module_name
  entrypoint: PluginClass
  dependencies:
    dependency_name:
      mode: pypi
      package: package-name
      version: package version      # Optional (uses latest)
      extras: [list, of, extras]    # Optional ([])

settings:
  field_id:
    type: string
    name: Friendly Name
    icon: tabler-icon-name          # Optional (no icon)
    default: "default value"        # Optional (empty)
    placeholder: "example text"     # Optional (empty)
    required: false                 # Optional (false)
  field_id:
    type: number
    name: Friendly Name
    icon: tabler-icon-name          # Optional (no icon)
    default: 0                      # Optional (0)
    placeholder: "example text"     # Optional (empty)
    required: false                 # Optional (false)
    min: null                       # Optional (null)
    max: null                       # Optional (null)
  field_id:
    type: switch
    name: Friendly Name
    icon: tabler-icon-name          # Optional (no icon)
    default: false                  # Optional (false)
    placeholder: "example text"     # Optional (empty)
    required: false                 # Optional (false)
```