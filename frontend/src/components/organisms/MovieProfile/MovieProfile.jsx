import React from 'react';
import styles from './MovieProfile.module.css';
import MovieTitleContainer from "../../molecules/MovieTitleContainer/MovieTitleContainer";
import MovieCastList from "../../molecules/MovieCastList/MovieCastList";
import MovieMeta from "../../molecules/MovieMeta/MovieMeta";
import PosterImage from "../../atoms/PosterImage/PosterImage";
import VideoBox from "../../atoms/VideoBox/VideoBox";
import StreamingProviderList from "../../molecules/StreamingProviderList/StreamingProviderList";

function MovieProfile({title, synopsis, director, releaseDate, cast, poster, trailer, streaming_providers}) {
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