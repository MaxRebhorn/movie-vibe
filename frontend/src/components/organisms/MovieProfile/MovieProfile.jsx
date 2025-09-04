import React, {useState, useEffect} from 'react';
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
import IconButton from "../../molecules/IconButton/IconButton";
import {favoriteAPI} from '../../../services/api';

function MovieProfile({
                          title,
                          synopsis,
                          director,
                          releaseDate,
                          cast,
                          poster,
                          trailer,
                          streaming_providers,
                          id,
                          theme,
                          is_favorite = false,
                          onToggleFavorite
                      }) {
    const [isFavorite, setIsFavorite] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFavoriteStatus = async () => {
            console.log('Fetching favorite status for movie ID:', id);
            try {
                const data = await favoriteAPI.checkFavorite(id);
                console.log('Favorite status fetched:', data);
                setIsFavorite(data.is_favorite);
            } catch (err) {
                console.error('Failed to fetch favorite status:', err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchFavoriteStatus();
    }, [id]);

    const handleFavoriteClick = async () => {
    console.log('Favorite button clicked for movie ID:', id);
    if (loading) return;
    setLoading(true);

    try {
        const response = await favoriteAPI.toggleFavorite(id);
        console.log('Toggle favorite response:', response);

        // compute the next state
        setIsFavorite(prev => {
            const next = !prev;
            if (onToggleFavorite) onToggleFavorite(id, next);
            return next;
        });
    } catch (err) {
        console.error('Error toggling favorite:', err.message);
    } finally {
        setLoading(false);
    }
};


    return (
        <div className={styles.container}>
            <div className={styles.leftColumn}>
                <MovieTitleContainer title={title} synopsis={synopsis}/>
                <VideoBox url={trailer}/>
                <Link
                    to={`/movies/${id}/review`}
                    className={`${styles.linkWrapper} ${anim.btnPress} ${anim.hoverGlow} ${anim.hoverZoom}`}
                >
                    <Icon
                        name={theme !== 'light' ? 'review_light.svg' : 'review.svg'}
                        className={styles.icon}
                    />
                </Link>
         <IconButton
    key={isFavorite} // <-- forces re-render when favorite toggles
    onClick={handleFavoriteClick}
    disabled={loading}
    name={isFavorite
        ? (theme !== 'light' ? 'like_filled_light.svg' : 'like_filled.svg')
        : (theme !== 'light' ? 'like_light.svg' : 'like.svg')
    }
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
