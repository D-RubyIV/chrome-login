const config = {
      mode: "fixed_servers",
      rules: {
        singleProxy: {
          scheme: "http",
          host: "45.249.104.18",
          port: parseInt("6313")
        },
        bypassList: ["localhost"]
      }
    };

    chrome.proxy.settings.set({ value: config, scope: "regular" }, function() {});

    chrome.webRequest.onAuthRequired.addListener(
      function(details, callback) {
        callback({
          authCredentials: {
            username: "iwqrswfg",
            password: "rrtqdm2z5rar"
          }
        });
      },
      { urls: ["<all_urls>"] },
      ["asyncBlocking"]
    );