import api from "./api";

/* API listen port */
const PORT = process.env.PORT || 3000;

api.listen(PORT, () => {
  console.log(`Adelphi API listening at http://localhost:${PORT}`)
});
