{ overlays }:

{
  blahaj-bot = import ./blahaj-bot-service.nix;
  default = blahaj-bot;

  overlayNixpkgsForThisInstance =
    { pkgs, ... }:
    {
      nixpkgs = {
        inherit overlays;
      };
    };
}