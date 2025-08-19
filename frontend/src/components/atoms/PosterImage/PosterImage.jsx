import styles from "./PosterImage.module.css";

export default function PosterImage({ src, alt }) {
  return <img className={styles.poster} src={src} alt={alt} />;
}
