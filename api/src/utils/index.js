import fs from "fs";

/*
  Read a file synchronously at the specified path
  and returns its entire content.
*/
export function readDataFile(path) {
  var data;
  try {
    data = fs.readFileSync(path, 'utf8');
  } catch (err) {
    console.log('Could not read file ' + path);
    return {};
  }
  return JSON.parse(data);
}