import { getLanguage, setLanguage } from "../i18n"

export default function LanguageToggle({ className = "" }) {
  function toggle() {
    setLanguage(getLanguage() === "tr" ? "en" : "tr")
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className={`h-5 w-5 shrink-0 overflow-hidden rounded-full ${className}`}
      title={getLanguage() === "tr" ? "Switch to English" : "Türkçe'ye geç"}
    >
      <img
        src={getLanguage() === "tr" ? "/english.svg" : "/turkish.svg"}
        alt=""
        className="h-full w-full object-cover"
      />
    </button>
  )
}