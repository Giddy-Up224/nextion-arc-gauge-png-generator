# lib_template

## Setup

When you use this repo as a template, you'll wish to rename the relevant files and file contents to the new repo name and change the author `name` and `email` in `library.json`. Simply run the `init_repo_info.py` Python script to accomplish this task. *Beware, it will use your local `git config`'s `author` and `email` values for the `library.json`. If you wish to use a different name and email, change it manually afterwards.*


## What is lib_template?

- Provide a description of the use case for this repo...

## Code Style Guidelines

- Please use the `.clang-format` style. (You can automatically apply the style by selecting it from the context menu.)

<img src="img\format_document.png" alt="screenshot of context menu" width="250">

- Use the [`esp_log_alias`](https://github.com/Rubix-Battery/esp_log_alias) library (an alias for `ESP_LOGI`, `ESP_LOGD`, etc.). rather than `Serial.println()` etc. (see [official documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/log.html) for instructions on use.)

## Links and Resources

- Provide links and References to material that is relevant to the project...

## Credits

- Give credit where credit is due...