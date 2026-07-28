# RPM Building with Docker

This Dockerfile provides a clean Fedora environment for building and testing RPMs without polluting your local system.

## Build the Docker image

```bash
docker build -t lmslogger-rpmbuild .
```

## Validate the spec file

```bash
docker run --rm -v "$(pwd):/workspace" lmslogger-rpmbuild rpmlint lmslogger.spec
```

## Build the RPM

First, create the source tarball:

```bash
VERSION=$(grep ^Version: lmslogger.spec | sed -e 's/^Version: //')
git archive --format tgz HEAD . --prefix lmslogger-${VERSION} \
  -o lmslogger-0.1.5.tar.gz HEAD
```

Then run the build inside the container:

```bash
docker run --rm -v "$(pwd):/workspace" lmslogger-rpmbuild -c \
  "cd /workspace && rpmbuild -ba lmslogger.spec"
```

The RPM will be created in `~/rpmbuild/RPMS/noarch/`.

## One-liner to build and check

```bash
docker run --rm -v "$(pwd):/workspace" lmslogger-rpmbuild -c \
  "git archive --exclude=.instructions.md --exclude=docs/ -o lmslogger-0.1.5.tar.gz HEAD && \
   cp lmslogger-0.1.5.tar.gz ~/rpmbuild/SOURCES/ && \
   cp lmslogger.service ~/rpmbuild/SOURCES/ && \
   cp lmslogger.env ~/rpmbuild/SOURCES/ && \
   rpmlint lmslogger.spec && \
   rpmbuild -ba lmslogger.spec"
```

## Troubleshooting

If rpmbuild complains about missing sources, ensure `Source0`  files are in `~/rpmbuild/SOURCES/` within the container.
