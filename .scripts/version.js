#!/usr/bin/env node

const path = require("path");
const { readdir, readFile, writeFile } = require("fs").promises;
const { re } = require("re-template-tag");

const ENC = "utf-8";

const resolve = (...args) => path.resolve(__dirname, '..', ...args);

const FILES = [
  "./_data/authors.yml",
  "./CHANGELOG.md",
  "./download.md",
  "./README.md",
  "./thank-you.md",
].map(f => resolve(f));

const COPY_FILES = [
  "LICENSE.md",
  "NOTICE.md",
];

const RE_TAG = /\{[:%][^}]*\}/g;
const RE_TOC = /(\d+\.|\*) this list will be replaced by the toc/ig;

const RE_FM_BEGIN = /^---/; // beginning front matter at beginning of file
const RE_FM_END = /---/; // end of front matter
const RE_CONTENT = /(.|\n)*?/; // arbitrary content, nongreedy (!), captured
const FRONT_MATTER_REGEX = re`/${RE_FM_BEGIN}${RE_CONTENT}${RE_FM_END}/u`;

// <https://stackoverflow.com/a/45130990/870615>
async function getFiles(dir) {
  const dirents = await readdir(dir, { withFileTypes: true });
  const files = await Promise.all(dirents.map((dirent) => {
    const res = resolve(dir, dirent.name);
    return dirent.isDirectory() ? getFiles(res) : res;
  }));
  return Array.prototype.concat(...files);
}

(async function main() {
  try {
    const {
      version: vNext,
      prevVersion: vPrev,
    } = JSON.parse(await readFile(resolve("./#jekyll-theme-hydejack/assets/version.json"), ENC));

    console.log(vNext, vPrev);

    const prev = vPrev.replace(/\./g, "\\.");
    const prevRegExp = new RegExp(prev, "g");

    const args = await Promise.all([
      getFiles(resolve("./hyde/_posts")),
      getFiles(resolve("./hydejack/_posts")),
      getFiles(resolve("./_projects")),
      getFiles(resolve("./docs")),
    ]);
      
    await Promise.all(
      Array.prototype.concat.call(FILES, ...args)
        .filter(([f]) => !f.startsWith("."))
        .map(f => [f, readFile(f, ENC)])
        .map(async ([f, p]) => {
          const content = await p;

          if (f.includes("CHANGELOG")) {
            const pattern = new RegExp(`([^v])${prev}`, "g");
            return [f, content.replace(pattern, `$1${vNext}`)];
          }

          const cleanContent = content.replace(prevRegExp, vNext);
          return writeFile(f, cleanContent, ENC);
        }));

    await Promise.all(COPY_FILES
      .map(f => [f, readFile(f, ENC)])
      .map(async ([f, p]) => {
        const content = await p;
        const cleanContent = content.replace(RE_TAG, '').replace(RE_TOC, '').replace(FRONT_MATTER_REGEX, '');
        return writeFile(resolve('./#jekyll-theme-hydejack', f), cleanContent, ENC);
      }));

    process.exit(0);
  } catch (e) {
    console.error(e); // eslint-disable-line
    process.exit(1);
  }
})();
