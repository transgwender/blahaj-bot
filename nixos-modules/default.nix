{ overlays }:

{
  blahaj-bot = import ./blahaj-bot-service.nix;

  overlayNixpkgsForThisInstance =
    { pkgs, ... }:
    {
      nixpkgs = {
        inherit overlays;
      };
    };
}