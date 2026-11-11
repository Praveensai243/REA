# @sipp_smart — 45 days of Shorts, free and automatic

Every day at about **6:45 PM India time**, GitHub makes that day's Telugu Short
(voice + music + text) and posts it to Instagram as a Reel. YouTube Shorts are
made in batches here and you schedule them in YouTube Studio.

Cost: **₹0 / $0.** GitHub Actions, the Microsoft Telugu voice, HyperFrames and
Instagram's official API are all free.

| What | Where |
|---|---|
| The 45 scripts (edit text here) | `content/calendar.yaml` |
| Video maker | `scripts/make_video.py` |
| Instagram poster | `scripts/post_instagram.py` |
| Daily posting | `.github/workflows/daily-instagram.yml` |
| YouTube batch | `.github/workflows/make-youtube-batch.yml` |
| Proof of each post | `posted/<date>.json` (added automatically) |

---

## One-time setup (about 30 minutes)

### Step 1 — Make @sipp_smart a professional account
Instagram app → Settings → Account type and tools → switch to **Business**
(Creator also works for most accounts, but Business is the safest for posting by API).

### Step 2 — Get your Instagram token (free)
1. Go to **developers.facebook.com** → log in → **My Apps** → **Create app**.
2. Pick the use case **"Manage messaging & content on Instagram"**. Give the app any name (e.g. *sipp smart poster*).
3. Open **API setup with Instagram login** → **Generate access tokens** → **Add account** → log in as **@sipp_smart** and allow access.
4. Copy two things:
   - the **Instagram user ID** (a long number shown next to the account)
   - the **access token** (long text starting with `IG…`)
5. Keep the app in **Development** mode. You don't need App Review to post to your own account.

The token works for **60 days**, which covers all 45 days. If you continue after
that, generate a new token and replace it in Step 4.

### Step 3 — Put this project on GitHub
1. On github.com create a **new public repository** named `sipp-smart-shorts`.
   (It must be public so Instagram can fetch each video from a public link.
   Your token stays secret, see Step 4.)
2. Upload all the files from this folder, keeping the folders as they are,
   or ask Claude to push them for you.

### Step 4 — Add the secrets
Repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Name | Value |
|---|---|
| `IG_USER_ID` | the Instagram user ID from Step 2 |
| `IG_ACCESS_TOKEN` | the access token from Step 2 |
| `PIXABAY_API_KEY` | your free Pixabay key, see Step 4b (video clips + photos) |
| `HF_TOKEN` | your Hugging Face **Read** token (after accepting the IndicF5 terms) |
| `VOICE_KEY` | the voice key Claude gave you (unlocks your encrypted voice sample) |

Then **Settings → Actions → General → Workflow permissions → Read and write** → Save.

### Step 4b — Free video clips and photos (Pixabay, 2 minutes)
1. Sign up free at **pixabay.com** → open **pixabay.com/api/docs** → your key is shown under **Parameters → key**.
2. Add it as the `PIXABAY_API_KEY` secret.

Each scene's centre card then plays a short, muted Pixabay **video clip** found with the day's
`broll:` search words. If no good clip turns up, it uses a Pixabay photo instead; without any key,
the cards show animated icons. Pixabay content is free to use, even commercially, with no credit
required (avoid clips with clear brand logos). A `PEXELS_API_KEY` also works for photos.
**Your own clips or photos:** put .mp4/.mov/.jpg/.png files in `content/photos/<date>/`; they are used first.

### Step 4c — Your own voice (voice cloning, free)
Videos are spoken in **your voice** using AI4Bharat **IndicF5** (MIT license, supports Telugu).
1. On huggingface.co open **ai4bharat/IndicF5** → **Agree and access repository**.
2. **Settings → Access Tokens → Create new token → Read** → add it as the `HF_TOKEN` secret.
3. Add the `VOICE_KEY` secret (Claude gave it to you). Your voice sample is stored **encrypted**
   (`content/voice/reference.wav.gpg`), so nobody can copy your voice from the public repo.
If cloning fails on a day, that video uses the free Microsoft Telugu voice so the post still goes out.

### Step 5 — Test it
1. **Actions** tab → **Daily Instagram Reel** → **Run workflow** → tick **dry run** → Run.
   After about 5 minutes, open the run and download the video under **Artifacts**. Check it.
2. Run it again **without** dry run. The Reel appears on @sipp_smart. 🎉
3. From now on it runs by itself every evening. If a day is already posted, it skips it,
   so it never posts twice.

---

## YouTube Shorts (about 15 minutes every 2 weeks)
YouTube's free API locks videos uploaded by personal apps as **private**, so YouTube
is scheduled by hand in YouTube Studio. YouTube Studio scheduling itself is free.

1. **Actions** → **Make videos for YouTube (batch)** → **Run workflow** → choose a date range (e.g. 2 weeks).
2. When it finishes, download the zip from **Artifacts**.
3. Open **studio.youtube.com** → **Create → Upload videos** → select the MP4s.
4. For each one, copy the **title** and **description** from `youtube_schedule.csv`,
   then choose **Schedule** with that row's date at 7:00 PM.

---

## Changing things
- **Your logo:** put your logo file in `template/assets/` named `logo.png` (a transparent PNG
  looks best; `logo.svg` / `logo.jpg` also work). Every video then shows it in the top-right
  corner. Without a logo file, a "@sipp_smart" badge is shown instead. To change its size, add
  `SIPP_LOGO_HEIGHT: 150` under `env:` in the workflow (default 120).
- **Look:** modelled on your reference reel: word-by-word captions at the top synced to the voice
  (one key word per line in colour), a floating photo card in the middle with slow zoom, MYTH/FACT
  chips, recipe checklists, and the comment question on the last card.
- **Animated icons:** every hook gets a moving icon that fits the topic (whisky glass filling, beer
  bubbles, coffee steam, car, gavel…). To force one, add `icon: whisky` (or beer, wine, cocktail,
  highball, coffee, bottle, shaker, water, moon, car, pill, gavel, palm, heart, thermo, tree,
  clock, bolt, question) to a scene.
- **Every video:** a bold hook in the first 2 seconds, a MYTH/FACT/TIP reveal with a build-up,
  drop and impact sound, and a comment question at the end (`ask:` in the calendar).
  The music is made fresh for each day: a hip-hop beat Mon–Thu and a deep-house groove Fri–Sun,
  with a 5-note "Sipp Smart" tune at the start and end. It's mastered to Instagram/YouTube loudness.
- **Weekly pattern:** Mon–Thu are education (health, laws, history, facts). Fri–Sun are cocktails
  and bottle picks.
- **Edit a video's text:** change it in `content/calendar.yaml` and commit. That day's video uses the new text.
- **Female voice:** in `daily-instagram.yml`, add `SIPP_VOICE: te-IN-ShrutiNeural` under `env:`.
- **Posting time:** change the `cron` line. It uses UTC time; India is UTC + 5:30.
- **Pause:** Actions → Daily Instagram Reel → **⋯ → Disable workflow**.

## If something goes wrong
- Each run shows a red ❌ with the reason. GitHub also emails you when a run fails.
- **"Invalid OAuth access token":** the token expired or was copied wrong. Make a new one (Step 2) and update the secret.
- **"could not process the video from any link":** run it again from the Actions tab. It's usually a temporary Instagram hiccup.
- Missed a day? Actions → Daily Instagram Reel → Run workflow → enter that date.
