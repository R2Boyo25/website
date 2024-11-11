# The Apricot CMS

The Apricot CMS is a Django-based CMS written in Python. It's very early in development and has a lot of issues that need to be resolved as of now.

## To-Do

- [ ] Add profile pages.
- [ ] Improve the image system.
- [ ] Add a real editor.
- [ ] Add a component system (w/ Lua)
- [ ] Add a theming system to allow editing the styling and HTML from the web interface.

## Installing

### Clone the repository

```bash
git clone https://github.com/r2boyo25/apricot
cd apricot
```

### Install the dependencies

If you're on NixOS, you can use `nix-shell` to get a shell with the necessary dependencies (other than the python libraries) installed.

[Install Poetry](https://python-poetry.org/docs/#installation) if you have not done so already, and then install the Apricot dependencies with:
```bash
poetry install --no-root
```

You'll also need to install `lessc` (the Node.js program) through your package manager or I dunno get it somehow.

### Collect the static files

```bash
poetry run python3 manage.py collectstatic
```

### Run the database migrations

```bash
poetry run python3 manage.py migrate
```

### Create a superuser account in Django

```bash
poetry run python3 manage.py createsuperuser
```

> [!IMPORTANT]  
> USERNAME SHOULD BE TITLE CASE ("Kazani" not "kazani" or "KAZANI")

Fill out any information it asks for — as of now, you can leave the email blank as the CMS doesn't use it for anything.

### Create a service for Apricot using your preferred method.

Docker container coming ~~soon~~ eventually, so for now I'd recommend SystemD (if you're trying to host this on Windows, how about you try Linux instead).

### Set up a proxy pass from NGINX, Caddy, or some other web server.

Django does not serve its own static files when in production mode, so do you remember those static files we collected earlier? (it created the `.collected-static` directory in the root of the repository)

You'll need to serve those under `/static` on your website (using the `try_files` directive in NGINX or equivalent).

You'll also need to proxy from the root of wherever you're trying to expose the CMS at (probably at the root of your domain, or a `blog.` subdomain?).

There's some Django config options that you'd need to set in `kazani/settings.py` if you wanted to move the static url or the website to somewhere else but I dunno what they are so you'd need to look them up yourself /shrug (sorry).

### Create your first page

At the moment, if you try to visit your webpage, it'll give you a 404 error because there's no page set for the homepage. You currently need to go to the page `/kaz/__admin_/login`, log in with the superuser account you created earlier, and then go Blog > Articles and create a new post. Fill out the fields and then set the page path to `/`.

I apologize for all the options — I tried to explain them for you in the UI :3

### Change Django settings

You need to generate a new secret with 
```bash
poetry run python3 manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
And then set `SECRET_KEY` to the returned string.
You should also set `DEBUG` to `False`.

Add
```py
CSRF_TRUSTED_ORIGINS = ["https://your.domain"]
```

To fix absolute URLs using `localhost` instead of your domain name (which will happen!), add
```py
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Adjust the styling and page layout [OPTIONAL]

HTML template files are in `templates` and the CSS files are in `static/style` (although they're `less` files). 

> [!IMPORTANT]  
> Keep in mind that when you change files under `static`, you'll need to re-run `poetry run python3 manage.py collectstatic` to regenerate the static files!!

> [!IMPORTANT]  
> You'll also need to swap out the favicon images as they're currently just my profile picture!!

I'd appreciate if you credit me in your footer or some where else e.g. with

```html
CMS and base styling by <a href="https://kazani.dev">Ohin "Kazani" Taylor</a>
```

## Uploads system

You can upload files or images to any location (the page field) in the Blog > Uploads page.

You can then refer to these from images or links (ONLY IN MARKDOWN; use full url from HTML) by using the url of `$ident` where ident is the ident you specified for the upload in the upload form.

## Questions?

Create an issue or [contact me](https://kazani.dev).