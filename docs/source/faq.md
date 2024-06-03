# FAQ

## django-viewcomponent vs django-components

1. **django-viewcomponent** is inspired by Rails [ViewComponent](https://viewcomponent.org/), focusing solely on encapsulating Django templates without concerning itself with other elements such as frontend assets or generating Django responses.
2. The `slot` field in **django-viewcomponent** can be invoked multiple times to pass collections.
3. In **django-viewcomponent**, slot fields are declared in the Python component file rather than in the template file, making the slot field more flexible and easier to maintain.
4. **django-viewcomponent** includes a preview feature that allows developers to easily create component previews.
