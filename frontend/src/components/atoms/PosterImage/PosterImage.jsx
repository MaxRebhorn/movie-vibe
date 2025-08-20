import styles from "./PosterImage.module.css";
import anim from '../../../styles/animation.module.css'
export default function PosterImage({ src, alt }) {
  return <img className={`${styles.poster} ${anim.hoverZoom} ${anim.fadeIn}`} src={src} alt={alt} />;
}
