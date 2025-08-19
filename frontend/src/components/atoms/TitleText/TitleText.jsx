import styles from "./TitleText.module.css";

export default function TitleText({ children }) {
  return <h1 className={styles.title}>{children}</h1>;
}
