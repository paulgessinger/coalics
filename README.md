# coalics [![Build Status](https://travis-ci.org/paulgessinger/coalics.svg?branch=master)](https://travis-ci.org/paulgessinger/coalics)

## Development

Use `docker-compose` like 

```console
docker-compose -f docker-compose.yml -f dev.yml up
```

**Don't** use sqlite, the migrations won't work because columns are dropped and created!