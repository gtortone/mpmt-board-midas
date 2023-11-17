let probe_in_progress = false;

function check_fe_running(fename) {
  var path = "/System/Clients";
  mjsonrpc_db_get_value(path)
    .then(function (rpc) {
      let hv_running = false;
      if (rpc.result.status[0] == 1) {
        let clients = rpc.result.data[0];
        for (let key in clients) {
          if (key.endsWith("/name")) {
            continue;
          }

          if (clients[key].name.startsWith(fename)) {
            hv_running = true;
          }
        }
      }

      if (!hv_running) {
        document.getElementById(`${fename}_stopped`).style.display = "block";
      } else {
        document.getElementById(`${fename}_stopped`).style.display = "none";
      }
      setTimeout(check_fe_running.bind(null, fename), 5000);
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
      setTimeout(check_fe_running.bind(null, fename), 5000);
    });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function handle_banner_probe() {
   probing = document.getElementById("probing")
   banner = document.getElementById("probing_banner")
   if(probing.innerText == 'y') {
      // HV probing in progress
      banner.style.display = ""
   } else {
      banner.style.display = "none"
   }
}

function getOnlineModulesArray() {
  mpmtid = localStorage.mpmtid; 
  return new Promise(function (resolve, reject) {
    mjsonrpc_db_get_values([`/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Online`])
      .then(function (rpc) {
        resolve(rpc.result.data[0]);
      })
      .catch(function (error) {
        mjsonrpc_error_alert(error);
      });
  });
}

function getOnlineModulesList() {
  mpmtid = localStorage.mpmtid; 
  return new Promise(function (resolve, reject) {
    mjsonrpc_db_get_values([`/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Online`])
      .then(function (rpc) {
        let mlist = [];
        blist = rpc.result.data[0];
        blist.map((el, i) => {
          el ? mlist.push(i) : 0;
        });
        resolve(mlist);
      })
      .catch(function (error) {
        mjsonrpc_error_alert(error);
      });
  });
}

function getOnModulesList() {
  mpmtid = localStorage.mpmtid;
  return new Promise(function (resolve, reject) {
    mjsonrpc_db_get_values([
      `/Equipment/MPMT-RunControl${mpmtid}/Settings/Power enable`,
    ])
      .then(function (rpc) {
        let mlist = [];
        mask = rpc.result.data[0];
        for (let i = 0; i < 19; i++) if ((mask & (1 << i)) != 0) mlist.push(i);
        resolve(mlist);
      })
      .catch(function (error) {
        mjsonrpc_error_alert(error);
      });
  });
}

function getOC(value, ch) {
  return (value & (1 << ch)) >> ch ? true : false;
}

function HVProbe() {
  mpmtid = localStorage.mpmtid;
  if (authuser()) {
    (async () => {
      probe_in_progress = true;
      // start probing
      await mjsonrpc_db_set_value(
        `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Probe modules`,
        true
      ).catch((error) => {
        mjsonrpc_error_alert(error);
      });

      // waiting for probing
      let probing = true;
      while (probing) {
        await mjsonrpc_db_get_values([
          `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Probe modules`,
        ])
          .then((rpc) => {
            probing = rpc.result.data[0];
          })
          .catch((error) => {
            mjsonrpc_error_alert(error);
          });
        await sleep(2000);
      }
      probe_in_progress = false;
    })();
  }
}

function getHVStatusAll(value) {
  if (probe_in_progress) return;
  let str = "UNK";
  getOnModulesList().then((modules) => {
    modules.map((ch) => {
      switch (value[ch]) {
        case 0:
          str = "UP";
          break;
        case 1:
          str = "DOWN";
          break;
        case 2:
          str = "RUP";
          break;
        case 3:
          str = "RDN";
          break;
        case 4:
          str = "TUP";
          break;
        case 5:
          str = "TDN";
          break;
        case 6:
          str = "TRIP";
          break;
        default:
          break;
      }
      document.getElementById("hvstatus" + ch).innerHTML = str;
    });
  });
}

function getHVAlarmAll(value) {
  if (probe_in_progress) return;
  getOnModulesList().then((modules) => {
    modules.map((ch, i) => {
      let str = "";
      if (value[i] == 0) {
        str = "none";
      } else {
        if (value[i] & 1) str = str + "OV ";
        if (value[i] & 2) str = str + "UV ";
        if (value[i] & 4) str = str + "OC ";
        if (value[i] & 8) str = str + "OT ";
      }
      document.getElementById("hvalarm" + ch).innerHTML = str;
    });
  });
}

/*
 * adc mask functions
 */

function adcmask_to_checkboxes() {
  if (probe_in_progress) return;
  let mask = parseInt(document.getElementById("adc_mask").innerText);
  getOnlineModulesList().then((modules) => {
    modules.map((ch) => {
      document.getElementById("adc" + ch).checked = mask & (1 << ch);
    });
  });
}

function checkboxes_to_adcmask() {
  mpmtid = localStorage.mpmtid;
  if (probe_in_progress) return;
  getOnlineModulesList().then((modules) => {
    let mask = 0;
    modules.map((ch) => {
      let el = document.getElementById("adc" + ch);
      if (el.checked) {
        mask |= 1 << ch;
      }
    });

    // Avoid negative hex values in JS.
    mask = mask >>> 0;

    //mjsonrpc_db_set_value(`/Equipment/MPMT-RunControl${mpmtid}/Settings/Enable ADC sampling`,mask).catch((error) => {mjsonrpc_error_alert(error);});
  });
}

/*
 * power mask functions
 */

function check_poweroff(ch) {
  mpmtid = localStorage.mpmtid; 
  // check power-off request
  cb = document.getElementById("pw" + ch);
  if (cb.checked == false) {
    mjsonrpc_db_get_values([`/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Status`])
      .then((rpc) => {
        let status = rpc.result.data[0][ch];
        if (status != 1) {
          // 1: DOWN
          showFailure(
            `HV module ${ch} is not down. Please shutdown HV before power down`
          );
          cb.checked = true;
        }
        checkboxes_to_powermask();
      })
      .catch((error) => {
        mjsonrpc_error_alert(error);
      });
  } else checkboxes_to_powermask();
}

function powermask_to_checkboxes() {
  if (probe_in_progress) return;
  let mask = parseInt(document.getElementById("power_mask").innerText);
  getOnlineModulesList().then((modules) => {
    modules.map((ch) => {
      document.getElementById("pw" + ch).checked = mask & (1 << ch);
      handle_adc_checkbox(ch);
    });
    checkboxes_to_adcmask();
  });
}

function checkboxes_to_powermask() {
  mpmtid = localStorage.mpmtid;
  if (probe_in_progress) return;
  getOnlineModulesList().then((modules) => {
    let mask = 0;
    modules.map((ch) => {
      let el = document.getElementById("pw" + ch);
      if (el.checked) {
        mask |= 1 << ch;
      }
      handle_adc_checkbox(ch);
    });
    checkboxes_to_adcmask();

    // Avoid negative hex values in JS.
    mask = mask >>> 0;

    mjsonrpc_db_set_value(
      `/Equipment/MPMT-RunControl${mpmtid}/Settings/Power enable`,
      mask
    ).catch((error) => {
      mjsonrpc_error_alert(error);
    });
  });
}

function authuser() {
  var pass = "1234";
  var str = prompt("please enter the admin password:");
  if (str == pass) {
    return true;
  }
  showFailure("(wrong password)");
  return false;
}

function showSuccess(info = "") {
  Toastify({
    text: `Operation successfully completed\n${info}`,
    style: {
      background: "green",
    },
    position: "right",
    gravity: "top",
  }).showToast();
}

function showFailure(info = "") {
  Toastify({
    text: `Operation failed\n${info}`,
    style: {
      background: "red",
    },
    position: "right",
    gravity: "top",
  }).showToast();
}

function SetHV() {
  mpmtid = localStorage.mpmtid;
  if (authuser()) {
    voltage = parseInt(prompt("Please enter the HV value (V):", ""));
    getOnlineModulesList().then((modules) => {
      modules.map((ch) => {
        mjsonrpc_db_set_value(
          `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Vset[${ch}]`,
          voltage
        );
      });
    });
    showSuccess();
  }
}

function EnHV() {
  mpmtid = localStorage.mpmtid;
  if (authuser()) {
    getOnlineModulesList().then((modules) => {
      let mask = 0;
      modules.map((ch) => {
        mask += 2 ** ch;
      });
      console.log(mask);
      mjsonrpc_db_set_value(
        `/Equipment/MPMT-RunControl${mpmtid}/Settings/Power enable`,
        mask
      );
    });
    showSuccess();
  }
}

function SetTh() {
  mpmtid = localStorage.mpmtid;
  if (authuser()) {
    thr = prompt("Please enter the Threshold value (mV):", "");
    getOnModulesList().then((modules) => {
      modules.map((ch) => {
        mjsonrpc_db_set_value(
          `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Trigger threshold[${ch}]`,
          thr
        );
      });
    });
    showSuccess();
  }
}

function EnableAll() {
  mpmtid = localStorage.mpmtid;
  if (authuser()) {
    getOnlineModulesList().then((modules) => {
      let mask = 0;
      modules.map((ch) => {
        mask += 2 ** ch;
      });
      mjsonrpc_db_set_value(
        `/Equipment/MPMT-RunControl${mpmtid}/Settings/Power enable`,
        mask
      );
      //mjsonrpc_db_set_value(`/Equipment/MPMT-RunControl${mpmtid}/Settings/Enable ADC sampling`,mask);
    });
    showSuccess();
  }
}

function HVon(index) {
  mpmtid = localStorage.mpmtid;
  path = `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Power command[${index}]`;
  mjsonrpc_db_paste([path], ["on"])
    .then(function (rpc) {
      showSuccess();
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
    });
}

function HVoff(index) {
  mpmtid = localStorage.mpmtid;
  path = `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Power command[${index}]`;
  mjsonrpc_db_paste([path], ["off"])
    .then(function (rpc) {
      showSuccess();
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
    });
}

function HVReset(index) {
  mpmtid = localStorage.mpmtid;
  path = `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Power command[${index}]`;
  mjsonrpc_db_paste([path], ["reset"])
    .then(function (rpc) {
      showSuccess();
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
    });
}

function Pulser_freq(value, element) {
  let pulser = 1000 / value;
  element.childNodes[0].value = pulser;
  return true;
}

function SetClk(value) {
  mpmtid = localStorage.mpmtid;
  Paths = [
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock int-ext select`,
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock int-ext auto select`,
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Reference clock A-B select`,
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock A-B auto select`,
  ];
  mjsonrpc_db_paste(Paths, [0, 0, value, 0])
    .then(function (rpc) {
      showSuccess();
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
    });
}

function SetClkInt() {
  mpmtid = localStorage.mpmtid;
  Paths = [
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock int-ext select`,
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock int-ext auto select`,
  ];
  mjsonrpc_db_paste(Paths, [1, 0])
    .then(function (rpc) {
      showSuccess();
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
    });
}

function SetClkInt() {
  Paths = [
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock int-ext select`,
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock int-ext auto select`,
  ];
  mjsonrpc_db_paste(Paths, [1, 0])
    .then(function (rpc) {
      showSuccess();
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
    });
}

function SetClkAuto() {
  Paths = [
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock A-B auto select`,
    `/Equipment/MPMT-RunControl${mpmtid}/Settings/Clock int-ext auto select`,
  ];
  mjsonrpc_db_paste(Paths, [1, 1])
    .then(function (rpc) {
      showSuccess();
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
    });
}

function handle_adc_checkbox(ch) {
  let power_enabled = document.getElementById(`pw${ch}`).checked;
  if (power_enabled) {
    /* user power on channel:
     * - show channel metrics
     */
    let elems = document.getElementsByClassName(`hidewhenoff${ch}`);
    for (let i = 0; i < elems.length; i++) elems[i].style.display = "";
  } else {
    /* user power off channel :
     * - disable ADC sampling
     * - hide channel metrics
     */
    let adc_input = document.getElementById(`adc${ch}`);
    adc_input.checked = false;
    let elems = document.getElementsByClassName(`hidewhenoff${ch}`);
    for (let i = 0; i < elems.length; i++) elems[i].style.display = "";
  }
}
