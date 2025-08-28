import TitleText from "../../atoms/TitleText/TitleText";
import style from "./MovieTitleContainer.css"
import BodyText from "../../atoms/BodyText/BodyText"
export default function MovieTitleContainer({ title,synopsis }) {
  return <div style={style.container}>
    <TitleText>{title}</TitleText>
    <BodyText>{synopsis}</BodyText>
  </div>;
}
