# How to trigger

### auto-release

```shell
git tag -a v<your-version> -m "your-release-title"
git push origin v<your-version>
# That's it! It will automatically create a new release for you.
```

If you have to redo a release you'll need to delete the tags and push again

```shell
# Example only, you must replace the version and message with your message
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0   # delete remote tag
git tag -a v1.1.0 -m "Enhanced file name pattern"
git push origin v1.1.0
```