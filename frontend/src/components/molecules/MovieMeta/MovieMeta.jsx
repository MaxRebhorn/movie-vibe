import styles from "./MovieMeta.module.css";
import MetaText from "../../atoms/MetaText/MetaText";

export default function MovieMeta({ director, releaseDate }) {
  return (

    <div className={styles.metaContainer}>
      <MetaText label="Director" value={director} />
      <MetaText label="Release Date" value={releaseDate} />
    </div>
  );
}
