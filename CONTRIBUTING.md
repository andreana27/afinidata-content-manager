# How to contribute

Thank you for your interest in Afinidata! We are quite glad of you reading this, as Afinidata is an open project, and while it is not actively looking for volunteers, your support is quite appreciated. Please read throughly to ensure your contributions are the most effective.

Afinidata is built using several components, mainly including this, the content manager. Content manager holds the activities, user info and more. It is built on Python, using Django, so knowledge of both is highly recommended.

Here are some important resources:

  * [Afinidata Home Page](http://afinidata.com/) tells you what we are,
  * [Our Task list](#) Currently our tasks and roadmap are still run privately, we'll update it if it changes.
  * [Issue / Bug Tracker](https://github.com/afinidata2019/afinidata-content-manager/issues).
  * [Django Documentation](https://docs.djangoproject.com/en/2.2/)
  
## Running in development

Afinidata is fed with a large scale MySQL database in production, but we offer a small SQLite based demo DB for testing and development.
To run Afinidata on development:

    $ git clone https://github.com/afinidata2019/afinidata-content-manager/
    $ python manage.py runserver
    
## Testing

We use Django-Nose to run tests; Nose provides useful wrappers and tooling for better testing. To write tests however is the same as standard Django testing idioms. Please add at least a test for each feature in order to avoid lowering of our testing coverage score.

## Submitting changes

To add a new feature **send a [GitHub Pull Request](https://github.com/afinidata2019/afinidata-content-manager/pull/new/master) with a clear list of what you've done** (read more about [pull requests](http://help.github.com/pull-requests/)). 

When you send a pull request, please detail what and why is it useful. Fill the required fields on the PR template and ask for a reviewer's LGTM before merging to master.

Please follow our coding conventions (below) and make sure all of your commits are atomic (one feature per commit). If not it might be squashed and merged.

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."
    
## Documenting

We use Sphinx to autogenerate documentation. [https://afinidata-content-manager.readthedocs.io/]  It is needed to at least add docstrings to new member functions or classes.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to coc@afinidata.com


## Coding conventions

Start reading our code and you'll get the hang of it. We try to optimize for readability but we do have some pain points due to our legacy codebase.

  * Indent using two spaces (soft tabs)
  * Follow Django app convention
  * Avoid the use of advanced JS on views
  * We follow PEP-8 loosely, periodically run a linter to ensure uniform code formatting.
  * This is open source software. Consider the people who will read your code, and make it look nice for them. It's sort of like driving a car: Perhaps you love doing donuts when you're alone, but with passengers the goal is to make the ride as smooth as possible.
  * And More, pull requests regarding this, contributing or documentation are also quite appreciated


on behalf of Afini's team 
thanks again for your interest,
Sebastian, Tech @ Afinidata
