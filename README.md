# summerquest-site

Public pages for the SummerQuest app (Amazon Appstore listing): the landing page and the
privacy policy, served by GitHub Pages at https://zaclements-prog.github.io/summerquest-site/.

The policy's source of truth is `docs/store/privacy-policy.md` in the SummerQuest repo.
After changing it there, rebuild these pages and commit:

    python3 build.py ../summerquest/docs/store/privacy-policy.md .

`style.css` holds the shared look (the app's sky, cream cards and golden buttons). `fonts/` is
Fredoka (SIL Open Font License, `fonts/OFL.txt`), hosted here so the pages load nothing from
other websites. `img/` holds landing-page screenshots, resized from `docs/store/screenshots/`.
