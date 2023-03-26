import { Bard } from "./google-bard-lib";
import { perturb, perturbations } from 'perturbations';
import { articles } from 'articles';
import dotenv from 'dotenv-safe';
import { oraPromise } from 'ora';
import { readFileSync, writeFileSync } from 'fs';

dotenv.config();

/**
 * Test imperceptible perturbations against Google Bard Chatbot.
 *
 * ```
 * npx tsx google-bard.ts
 * ```
 */
async function main() {
  const api = new Bard(process.env.SECURE_COOKIE);

  let article_idx = 0;
  let perturb_idx = 0;
  let results = [];
  try {
    results = JSON.parse(readFileSync('results.json', 'utf8'));
    article_idx = Math.max(articles.indexOf(results.at(-1)['query']['title']), 0);
    perturb_idx = perturbations.indexOf(results.at(-1)['query']['technique']) + 1;
  } catch (err) {
    // Ignore missing file
  }

  while (article_idx < articles.length) {
    while (perturb_idx < perturbations.length) {
      const article = articles[article_idx];
      const perturbation = perturbations[perturb_idx];
      const prompt = perturb(article, perturbation);
      const res = await oraPromise(api.ask(prompt), {
        text: `${perturbation}: ${article}`
      });
      if (!res.response) {
        console.log('Query limit reached. Exiting.');
        return;
      }
      results.push({ 
        query: {
          title: article,
          technique: perturbation,
          prompt: prompt
        },
        result: res
      });
      writeFileSync('results.json', JSON.stringify(results, null, 2));
      perturb_idx++;
    }
    perturb_idx = 0;
    article_idx++;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
})
