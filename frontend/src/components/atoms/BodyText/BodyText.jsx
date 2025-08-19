import styles from "./BodyText.module.css";

export default function BodyText({ children }) {
  return <p className={styles.body}>{children}</p>;
}
