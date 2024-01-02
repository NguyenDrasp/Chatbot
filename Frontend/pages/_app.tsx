import "@/styles/globals.css";
import type { AppProps, AppContext } from "next/app";
import cookie from "cookie";
import { SSRKeycloakProvider, SSRCookies } from "@react-keycloak/ssr";
import type { IncomingMessage } from "http";

const keycloakCfg = {
  url: process.env.NEXT_PUBLIC_KEYCLOAK,
  realm: "sso",
  clientId: "ban-hang",
};

interface InitialProps {
  cookies: unknown;
}

function App({ Component, pageProps, cookies }: AppProps & InitialProps) {
  return (
    <SSRKeycloakProvider
      keycloakConfig={keycloakCfg}
      persistor={SSRCookies(cookies)}
      initOptions={{onLoad: "login-required"}}
    >
      <Component {...pageProps} />
    </SSRKeycloakProvider>
  );
}

function parseCookies(req?: IncomingMessage) {
  if (!req || !req.headers) {
    return {};
  }
  return cookie.parse(req.headers.cookie || "");
}

App.getInitialProps = async (context: AppContext) => {
  // Extract cookies from AppContext
  return {
    cookies: parseCookies(context?.ctx?.req),
  };
};

export default App;
