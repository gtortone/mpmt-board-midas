let online_channels = new Array(19).fill(false)
let power_channels = new Array(19).fill(false)
let adc_channels = new Array(19).fill(false)

let hvfe_running = false
let rcfe_running = false
let snfe_running = false

function check_fe_running(fename, mpmtid) {
  var path = "/System/Clients";
  mjsonrpc_db_get_value(path)
    .then(function (rpc) {
      let fe_running = false;
      if (rpc.result.status[0] == 1) {
        let clients = rpc.result.data[0];
        for (let key in clients) {
          if (key.endsWith("/name")) {
            continue;
          }
          if (clients[key].name.startsWith(`${fename}${mpmtid}`)) {
            fe_running = true;
          }
        }
      }

      if (!fe_running) {
        document.getElementById(`${fename}_stopped`).style.display = "block";
        if(fename.startsWith("snfe")) {
           snfe_running = false
           document.getElementById("mpmt_sensors").style.display = 'none'
        } else if(fename.startsWith("hvfe")) {
           hvfe_running = false
           document.getElementById("channels").style.display = 'none'
        } else if(fename.startsWith("rcfe")) {
           rcfe_running = false
           document.getElementById("mpmt_clk_control").style.display = 'none'
           document.getElementById("mpmt_acq_control").style.display = 'none'
        }
      } else {
        document.getElementById(`${fename}_stopped`).style.display = "none";
        if(fename.startsWith("snfe")) {
           snfe_running = true      
           document.getElementById("mpmt_sensors").style.display = 'block'
        } else if(fename.startsWith("hvfe")) {
           hvfe_running = true
           document.getElementById("channels").style.display = 'block'
        } else if(fename.startsWith("rcfe")) {
           rcfe_running = true
           document.getElementById("mpmt_clk_control").style.display = 'block'
           document.getElementById("mpmt_acq_control").style.display = 'block'
        }
      }
    })
    .catch(function (error) {
      mjsonrpc_error_alert(error);
      setTimeout(check_fe_running.bind(null, fename, mpmtid), 5000);
    });
}

function refresh_channels_status(arg) {
   
   jarg = Object()

   if (arg === undefined) {
      jarg.online = online_channels
      jarg.power = power_channels
      jarg.adc = adc_channels;   
   } else {
      jarg = JSON.parse(arg)
      online_channels = jarg.online;
      power_channels = jarg.power;
      adc_channels = jarg.adc;
   }

   jarg.online.forEach( (value, ch) => {
      if(value) {
         document.getElementById(`channel${ch}`).style.backgroundColor = ""    // online
         document.querySelectorAll(`.param${ch}`).forEach((el) => { el.style.display = ""})
         document.getElementById(`pwrbtn${ch}`).style="color: red";
         document.getElementById(`pwrbtn${ch}`).innerHTML="<b>OFF</b>";
      } else {
         document.getElementById(`channel${ch}`).style.backgroundColor = "#ff9ca6" // offline
         document.querySelectorAll(`.param${ch}`).forEach((el) => { el.style.display = "none"})
         document.getElementById(`pwrbtn${ch}`).style="color: green";
         document.getElementById(`pwrbtn${ch}`).innerHTML="<b>ON</b>";
      }
   });

   /*
   jarg.power.forEach( (value, ch) => { 
      document.getElementById(`pwr${ch}`).checked = value
   });
   */

   jarg.adc.forEach( (value, ch) => {
      document.getElementById(`adc${ch}`).checked = value
   });

   setTimeout(hvfe_rpc.bind(null, "get_channels_status", {}, refresh_channels_status, 1000), 2000);
}

function getOnlineModulesList() {
  mpmtid = localStorage.mpmtid; 
  return new Promise(function (resolve, reject) {
    mjsonrpc_db_get_values([`/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Online`])
      .then(function (rpc) {
        let mlist = [];
        blist = rpc.result.data[0];
        if (blist != null)
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
      `/Equipment/MPMT-RunControl${mpmtid}/Readback/Power enable`,
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

function getHVStatusAll(value) {
  let str = "UNK";
  let style = "";
  getOnModulesList().then((modules) => {
    modules.map((ch) => {
      switch (value[ch]) {
        case 0:
          str = "UP";
          style = "color: green"
          break;
        case 1:
          str = "DOWN";
          style = "color: gray"
          break;
        case 2:
          str = "RUP";
          style = "color: orangered"
          break;
        case 3:
          str = "RDN";
          style = "color: saddlebrown"
          break;
        case 4:
          str = "TUP";
          style = "color: orangered"
          break;
        case 5:
          str = "TDN";
          style = "color: saddlebrown"
          break;
        case 6:
          str = "TRIP";
          style = "color: red"
          break;
        default:
          break;
      }
      document.getElementById("hvstatus" + ch).innerHTML = `<b>${str}</b>`;
      document.getElementById("hvstatus" + ch).style = style;
    });
  });
}

function getHVAlarmAll(value) {
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

//
// RPC functions
//

function hvfe_rpc(cmd, args, callback, maxlen) {
   let params = Object()

   mpmtid = localStorage.mpmtid;
   params.client_name = `hvfe${mpmtid}`;
   params.cmd = cmd;
   params.args = JSON.stringify(args);
    
   if (maxlen !== undefined) {
      params.max_reply_length = maxlen;
   }
  
   mjsonrpc_call("jrpc", params).then(function(rpc) {
      let [status, reply] = parse_rpc_response(rpc.result);
      if (status == 1)
         callback(reply);
      else
        alert_rpc_error(status, reply);
   });
};

function parse_rpc_response(rpc_result) {
  let status = rpc_result.status;
  let reply = "";
  
  if (status == 1) {
    // Only get a reply from mjsonrpc if status is 1
    let parsed = JSON.parse(rpc_result.reply);
    status = parsed["code"];
    reply = parsed["msg"];
  }
  
  return [status, reply];
}

function alert_rpc_error(status, reply) {
   if(hvfe_running)
      dlgAlert("Failed to perform action!<div style='text-align:left'><br>Status code: " + status + "<br>Message: " + reply + "</div>"); 
}

function toggle_enable_bit(ch) {
   if (online_channels[ch-1] == false)
      call_set_enable_bit(ch, 1)
   else call_set_enable_bit(ch, 0)
}

function toggle_adc_bit(ch) {
   if (adc_channels[ch-1] == false)
      call_set_adc_bit(ch, 1)
   else call_set_adc_bit(ch, 0)
}

function set_enable_all(value) {
   if(authuser())
      call_set_enable_all(value)
}

function set_adc_all(value) {
   call_set_adc_all(value)
}

function set_enable_adc_all(value) {
   if(authuser()) {
      call_set_enable_adc_all(value)
   }
}

function call_set_enable_bit(ch, value) {

  mpmtid = localStorage.mpmtid;

  let params = Object()
  params.client_name = `hvfe${mpmtid}`
  params.cmd = "set_enable_bit"
  jargs = {"channel": ch, "value": value}
  params.args = JSON.stringify(jargs);
   
  mjsonrpc_call("jrpc", params).then(function(rpc) {
    let [status, reply] = parse_rpc_response(rpc.result);
    if (status == 1) {
      showSuccess();
    } else {
      showFailure()
    }
  }).catch(function(error) {
    mjsonrpc_error_alert(error);
  });
}

function call_set_enable_all(value) {

  mpmtid = localStorage.mpmtid;

  let params = Object()
  params.client_name = `hvfe${mpmtid}`
  params.cmd = "set_enable_all"
  jargs = {"value": value}
  params.args = JSON.stringify(jargs);
   
  mjsonrpc_call("jrpc", params).then(function(rpc) {
    let [status, reply] = parse_rpc_response(rpc.result);
    if (status == 1) {
      showSuccess();
    } else {
      showFailure()
    }
  }).catch(function(error) {
    mjsonrpc_error_alert(error);
  });
}

function call_set_enable_adc_all(value) {

  mpmtid = localStorage.mpmtid;

  let params = Object()
  params.client_name = `hvfe${mpmtid}`
  params.cmd = "set_enable_adc_all"
  jargs = {}
  params.args = JSON.stringify(jargs);
   
  mjsonrpc_call("jrpc", params).then(function(rpc) {
    let [status, reply] = parse_rpc_response(rpc.result);
    if (status == 1) {
      showSuccess();
    } else {
      showFailure()
    }
  }).catch(function(error) {
    mjsonrpc_error_alert(error);
  });
}

function call_set_adc_bit(ch, value) {

  mpmtid = localStorage.mpmtid;

  let params = Object()
  params.client_name = `hvfe${mpmtid}`
  params.cmd = "set_adc_bit"
  jargs = {"channel": ch, "value": value}
  params.args = JSON.stringify(jargs);
   
  mjsonrpc_call("jrpc", params).then(function(rpc) {
    let [status, reply] = parse_rpc_response(rpc.result);
    if (status == 1) {
      showSuccess();
    } else {
      showFailure()
    }
  }).catch(function(error) {
    mjsonrpc_error_alert(error);
  });
}

function call_set_adc_all(value) {

  mpmtid = localStorage.mpmtid;

  let params = Object()
  params.client_name = `hvfe${mpmtid}`
  params.cmd = "set_adc_all"
  jargs = {"value": value}
  params.args = JSON.stringify(jargs);
   
  mjsonrpc_call("jrpc", params).then(function(rpc) {
    let [status, reply] = parse_rpc_response(rpc.result);
    if (status == 1) {
      showSuccess();
    } else {
      showFailure()
    }
  }).catch(function(error) {
    mjsonrpc_error_alert(error);
  });
}

function call_cmd(ch, label) {

  mpmtid = localStorage.mpmtid;

  let params = Object()
  params.client_name = `hvfe${mpmtid}`
  params.cmd = "cmd"
  jargs = {"channel": ch, "cmd": label}
  params.args = JSON.stringify(jargs);
   
  mjsonrpc_call("jrpc", params).then(function(rpc) {
    let [status, reply] = parse_rpc_response(rpc.result);
    if (status == 1) {
      showSuccess();
    } else {
      showFailure()
    }
  }).catch(function(error) {
    mjsonrpc_error_alert(error);
  });
}

//
// helpers
//

function SetHV() {
  mpmtid = localStorage.mpmtid;
  if (authuser()) {
    voltage = parseInt(prompt("Please enter the HV value (V):", ""));
    getOnlineModulesList().then((modules) => {
      modules.map(async function(ch) {
        await mjsonrpc_db_set_value(
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
    mjsonrpc_db_set_value(
      `/Equipment/MPMT-HighVoltage${mpmtid}/Settings/Power enable`,
      Array(19).fill(true) 
    ).then( function(rpc) {
       showSuccess();
    });
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

//
// utility functions
//

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
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
