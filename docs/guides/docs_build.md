# building documentation – manual & ci

## manual build (local)

```bash
# activate venv with mkdocs-material installed
pip install mkdocs-material

# run live preview
mkdocs serve -a 0.0.0.0:8000

# export static site to /static/docs_site
mkdocs build -d static/docs_site
```

When you run the Flask app, browse `http://localhost:5000/docs/` and the blueprint will serve the static files.

## ci build (jenkins or github actions)

### jenkins pipeline snippet
```groovy
pipeline {
  agent docker {
    image 'squidfunk/mkdocs-material:latest'
  }
  stages {
    stage('Build docs') {
      steps {
        sh 'mkdocs build -d static/docs_site'
        archiveArtifacts artifacts: 'static/docs_site/**', fingerprint: true
      }
    }
    stage('Deploy to branch') {
      when { branch 'main' }
      steps {
        sh 'git add static/docs_site && git commit -m "docs: regenerate" || true'
        sh 'git push origin HEAD:docs-site'
      }
    }
  }
}
```

### github actions example
```yaml
name: docs-build

on:
  push:
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install mkdocs-material
      - run: mkdocs build -d static/docs_site
      - uses: actions/upload-artifact@v4
        with:
          name: docs_site
          path: static/docs_site
```

The `static/docs_site` folder is committed or shipped with the container image; Flask blueprint serves it on the same 5000/5001 ports.
