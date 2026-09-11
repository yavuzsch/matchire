import en from "./en"
import tr from "./tr"

const LANGUAGES = { tr, en }

export function getLanguage() {
  return localStorage.getItem("language") || "tr"
}

export function setLanguage(lang) {
  localStorage.setItem("language", lang)
  window.location.reload()
}

export const t = LANGUAGES[getLanguage()] || tr

export const EDUCATION_LEVELS = Object.keys(tr.educationLevels)
export const FIELDS = Object.keys(tr.fields)