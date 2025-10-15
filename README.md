### New:
- **Configurable automated users per git service** - You can now configure automated users/bots per service instead of using a hardcoded list
- Exclude Gerrit changes with no reviewers invited
- Refactoring all tests & Tox support
- Possibility of omitting WIP pull requests/merge requests in output with *--ignore-wip* argument
- Replace *-s, -v, -d* arguments with one argument *--age*

# review-rot
reviewrot is a CLI tool, that helps to list down open review requests from github, gitlab and gerrit.

## Sample I/P:
Create '~/.reviewrot.yaml'. browse the [examples](https://github.com/nirzari/review-rot/tree/master/examples/) for content.

## Installation
```shell
python setup.py install
```

Alternatively, for development:
```shell
python setup.py develop
```

## [NEW] Tests
You can use `tox` or `detox` to run the tests against Python 3.7+:
```shell
sudo dnf install python-detox
detox
```

## Script:

#### review-rot
```shell
> review-rot --help
usage: review-rot [-h] [-c CONFIG]
                  [--age {older,newer} [#y #m #d #h #min ...]]
                  [-f {oneline,indented,json}] [--show-last-comment [DAYS]]
                  [--reverse] [--sort {submitted,updated,commented}] [--debug]
                  [--ignore-wip] [-k] [--cacert CACERT]

Lists pull/merge/change requests for github, gitlab and gerrit

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file to use
  --age {older,newer} [#y #m #d #h #min ...]
                        Filter pull request based on their relative age
  -f {oneline,indented,json}, --format {oneline,indented,json}
                        Choose from one of a few different styles
  --show-last-comment [DAYS]
                        Show text of last comment and filter out pull requests
                        in which last comments are newer than specified number
                        of days
  --reverse             Display results with the most recent first
  --sort {submitted,updated,commented}
                        Display results sorted by the chosen event time.
                        Defaults to submitted
  --debug               Display debug logs on console
  --ignore-wip          Omit WIP PRs/MRs from output

SSL:
  -k, --insecure        Disable SSL certificate verification (not recommended)
  --cacert CACERT       Path to CA certificate to use for SSL certificate
                        verification
```

You can filter MRs/PRs based on their relative age
```
review-rot --age older 5d 10h
```
outputs MRs/PRs which were submitted more than 5 days and 10 hours ago
```
review-rot --age newer 5d 10h
```
outputs MRs/PRs which submitted in the last 5 days and 10 hours

You can use **--show-last-comment** flag to include the text of last comment with json format:
```
review-rot -f json --show-last-comment
```

## Web UI

There is a static html+js web interface that can read in the output of the
`review-rot` CLI tool and produce a web page:

First, set up a *cron job* to run review-rot every (say) 15 minutes:

```shell
*/15 * * * * review-rot -f json > /home/someuser/public_html/reviewrot/data.json
```

Then, modify `web/js/site.js` to point the data url to the location of your new file.

## Automated PR/MR Categorization

review-rot can categorize PRs/MRs as automated when the `categorize_automated` argument is enabled. You can configure which users/bots should be considered automated on a per-service basis.

### Configuration

Add an `automated_users` list to each git service in your configuration:

```yaml
git_services:
  - type: github
    token: my_github_token
    repos:
       - user_name/repo_name
    # Configure automated users/bots for this GitHub service
    automated_users:
       - renovate[bot]
       - dependabot[bot]
       - github-actions[bot]
       - codecov[bot]

  - type: gitlab
    token: my_gitlab_token
    host: https://gitlab.com
    repos:
        - group_name/project_name
    # Configure automated users/bots for this GitLab service
    automated_users:
       - gitlab-bot
       - renovate-bot
       - ci-bot

arguments:
  # Enable automated categorization
  categorize_automated: true
```

### Backward Compatibility

If `automated_users` is not specified for a service, review-rot will use the default hardcoded list:
- `renovate[bot]`
- `dependabot[bot]`
- `red-hat-konflux[bot]`
- `ec-automation[bot]`

### Usage

When `categorize_automated` is enabled, each PR/MR result will have an `is_automated` field indicating whether it was created by an automated user. This is useful for filtering or highlighting automated PRs in reports.

## Gerrit service

### [NEW] Exclude changes with no reviewers invited:

```
git_services:
  - type: gerrit
    reviewers:
      ensure: True
```

User accounts can be excluded from the reviewers list for the change, for example, to not count bot accounts as reviewers:

```
git_services:
  - type: gerrit
    reviewers:
      id_key: email
      excluded:
        - the.bot@example.com
```

`id_key` is the `FieldName` to get the value to identify the reviewer. If not set defaults to `username`.

`excluded` is a list of reviewers, identified by their `id_key` in the reviewers entity.

If `reviewers` is not empty and `ensure` is not defined, it's implicitly True.

ID values for `excluded` and `id_key` are the same as for [AccountInfo](https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#account-info).

## Usage

### Container

review-rot can be executed in a containerized environment. For example:

```bash
podman run -v /my/local/config.yaml:/reviewrot.yaml:z quay.io/lucarval/review-rot:latest --config /reviewrot.yaml
```

#### Verification

The review-rot container image is signed and attested. [cosign](https://github.com/sigstore/cosign)
version 2 is required.

To verify the image signature:

```bash
cosign verify quay.io/lucarval/review-rot:latest \
  --certificate-github-workflow-repository lcarva/review-rot \
  --certificate-identity 'https://github.com/lcarva/review-rot/.github/workflows/package.yaml@refs/heads/main' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com'
```

To verify the image SBOM attestation:

```bash
cosign verify-attestation quay.io/lucarval/review-rot:latest \
  --type spdx \
  --certificate-github-workflow-repository lcarva/review-rot \
  --certificate-identity 'https://github.com/lcarva/review-rot/.github/workflows/package.yaml@refs/heads/main' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com'
```

To verify the image SLSA Provenance attestation:

```bash
cosign verify-attestation quay.io/lucarval/review-rot:latest \
  --type slsaprovenance \
  --certificate-github-workflow-repository lcarva/review-rot \
  --certificate-identity 'https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@refs/tags/v2.1.0' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com'
```
