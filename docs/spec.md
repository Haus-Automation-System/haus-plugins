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
      extras: [list, of, extras]    # Optional
```