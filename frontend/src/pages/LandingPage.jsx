import { Navigation } from '../components/organisms/Navigation';
import { ProductGrid } from '../components/organisms/ProductGrid';
import { SearchBar } from '../components/molecules/SearchBar';
import { Text } from '../components/atoms/Text';

export const LandingPage = () => {
  const products = [
    // Product data would go here
  ];

  return (
    <div className="landing-page-1">
      <Navigation />
      <Text variant="heading">MoVi</Text>
      <SearchBar />
      <ProductGrid products={products} />
    </div>
  );
};
