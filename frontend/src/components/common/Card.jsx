export default function Card({ children, className = "" }) {
  return <div className={`sd-card ${className}`}>{children}</div>;
}