{ overlays }:

rec {
  blahaj-bot = import ./blahaj-bot-service.nix;
  default = blahaj-bot;
}