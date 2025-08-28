import styles from "./MetaText.module.css";

export default function MetaText({ label, value }) {
  return (
    <span className={styles.meta}>
      <strong>{label}: </strong>{value}
    </span>
  );
}
