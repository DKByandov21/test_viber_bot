export function formatTime(isoString) {
  if (!isoString) return ""
  const date = new Date(isoString)
  return date.toLocaleString("bg-BG", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function timeAgo(isoString) {
  if (!isoString) return ""
  const diffMs = Date.now() - new Date(isoString).getTime()
  const minutes = Math.floor(diffMs / 60000)

  if (minutes < 1) return "точно сега"
  if (minutes < 60) return `преди ${minutes} мин`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `преди ${hours} ч`

  const days = Math.floor(hours / 24)
  return `преди ${days} дни`
}
