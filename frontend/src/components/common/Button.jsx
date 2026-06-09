export default function Button({
  children,
  variant = "primary",
  className = "",
  type = "button",
  ...props
}) {
  const variantClass = {
    primary: "sd-btn-primary",
    secondary: "sd-btn-secondary",
    ghost: "sd-btn-ghost",
    danger: "sd-btn-danger",
  }[variant];

  return (
    <button
      type={type}
      className={`sd-btn ${variantClass} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}