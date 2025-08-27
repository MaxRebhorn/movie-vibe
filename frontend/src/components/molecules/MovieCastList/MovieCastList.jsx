// StreamingProviderList.jsx
import styles from "./MovieCastList.module.css";
import Tag from "../../atoms/Tag/Tag";
import '../../../styles/colors.css';

export default function MovieCastList({ cast }) {
  return (
    <div className={styles.castList}>
        {cast.map((actorName, index) => (
            <Tag
              label={actorName}
              color="accent"
              size="small"
            />
        ))}
    </div>
  );
}