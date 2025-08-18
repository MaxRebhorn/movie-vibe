export const ProductGrid = ({ products }) => {
  return (
    <div className="product-grid">
      {products.map((product, index) => (
        <ProductCard
          key={index}
          title={product.title}
          director={product.director}
          tags={product.tags}
          image={product.image} // unified prop
        />
      ))}
    </div>
  );
};
