export default function StatusBadge({ status }) {
  const key = String(status || "").toUpperCase();

  const map = {
    OPEN: "sd-badge-open",
    IN_PROGRESS: "sd-badge-progress",
    CLOSED: "sd-badge-closed",
    ESCALATED: "sd-badge-escalated",
    HIGH: "sd-badge-high",
    MEDIUM: "sd-badge-medium",
    LOW: "sd-badge-low",
  };

  return (
    <span className={`sd-badge ${map[key] || "sd-badge-default"}`}>
      {key.replace("_", " ")}
    </span>
  );
}