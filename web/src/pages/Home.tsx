import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div>
      <h1>Welcome to Casa Cuenta</h1>
      <Link to={"/signup"}>Sign up</Link>
      <Link to={"/signin"}>Sign in</Link>
    </div>
  );
};

export default Home;
