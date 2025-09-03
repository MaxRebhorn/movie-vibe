import React from 'react';
import styles from './MovieProfile.module.css';
import MovieTitleContainer from "../../molecules/MovieTitleContainer/MovieTitleContainer";
import MovieCastList from "../../molecules/MovieCastList/MovieCastList";
import MovieMeta from "../../molecules/MovieMeta/MovieMeta";
import PosterImage from "../../atoms/PosterImage/PosterImage";
import VideoBox from "../../atoms/VideoBox/VideoBox";
import StreamingProviderList from "../../molecules/StreamingProviderList/StreamingProviderList";
import {Link} from "react-router-dom";
import anim from "../../../styles/animation.module.css";
import Icon from "../../atoms/Icon/Icon";

function MovieProfile({title, synopsis, director, releaseDate, cast, poster, trailer, streaming_providers,id,theme}) {
    return (
        <div className={styles.container}>
            <div className={styles.leftColumn}>
                <MovieTitleContainer
                    title={title}
                    synopsis={synopsis}
                ></MovieTitleContainer>
                <VideoBox
                    url={trailer}
                />
                  <Link to={`/movies/${id}/review`} className={`
                    ${styles.linkWrapper}
                    ${anim.btnPress}
                    ${anim.hoverGlow}
                    ${anim.hoverZoom}
                `}>
                    <Icon
                        name={theme !== 'light' ? 'review_light.svg' : 'review.svg'}
                        className={styles.icon}
                    />
                </Link>
            </div>
            <div className={styles.rightColumn}>
                <PosterImage src={poster} alt={title}/>

                <div className={styles.rightColumnContent}>
                    <MovieMeta director={director} releaseDate={releaseDate}/>
                    <MovieCastList cast={cast}/>
                    <StreamingProviderList providers={streaming_providers}/>
                </div>
            </div>

        </div>
    );
}

export default MovieProfile;