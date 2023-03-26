# Google Bard Chatbot
This directory contains scripts to run experiments against Google's Bard chatbot.

## Installation

Install node dependencies:
```sh
npm install .
```

Note that these scripts were written on Node v19.8.1.

In addition, install Python dependencies for graphing:
```sh
pip3 install -r requirements.txt
```

## Usage

To run the experiments, you must first obtain a fresh cookie from *bard.google.com* in a browser with a logged-in user that has access to the Google Bard preview. Use the cookie starting with `__Secure-`,for example `__Secure-1PSID`. This cookie value should then be copied into a `.env` file in this directory following the syntax given in `.env.example`. Be sure to include the name of the cookie, e.g.:
```sh
SECURE_COOKIE=__Secure-1PSID=abc123
```

Once this is complete, the Google Bard Chatbot experiments cna be launched with:
```sh
npx tsx google-bard.ts
```

Once the results have been obtained and serialized as a JSON file, they can be graphed with the following command:
```sh
./graphs.py results.json
```

The results used to create the visualizations in the associated paper are available in the `results/` subdirectory.