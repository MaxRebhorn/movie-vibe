export const ProductCard = ({ title, director, tags, image }) => {
  return (
    <div className="product-info-card">
      <img src={image} alt={title} />
      <div className="body">
        <Text variant="heading">{title}</Text>
        <Text variant="strong">{director}</Text>
        <Text variant="small">{tags}</Text>
      </div>
    </div>
  );
};
