# Changelog

## 1.0.9

1. Make `comopnent` argument in `Renders Fields` supports component registered name, component class, and function.
2. Remove `component_name` from `component` class.
3. Update the rendering logic to make it consistent.

## 1.0.8

1. Remove `outer_context` from component, using `context.push` to create isolated context for component.
2. Fix bug of using `include` in `call` tag.

## 1.0.7

1. Supports using components in pure Python code
2. Add doc about the `NameSpace`

## 1.0.6

1. Return 404 instead of raising exception if preview not found.
2. Use pre-commit to help format code.
3. Update doc about the `preview`

## 1.0.5

1. Add `show_previews` option to control whether to show previews or not

## 1.0.4

1. Add component `Preview` support

## 1.0.2

1. Initial release
