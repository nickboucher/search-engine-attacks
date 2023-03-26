/*
 * Original Author: Pawan Osman
 * Originally Published: github.com/PawanOsman/GoogleBard
 * Used with MIT license
 */
import vm from "vm";
import https from "https";
import { load } from "cheerio";
import axios, { AxiosInstance, AxiosRequestConfig } from "axios";

class Bard {
	private axios: AxiosInstance;
	private cookies: string = "";

	constructor(cookie: string) {
		this.cookies = cookie;

		const agent = new https.Agent({
			rejectUnauthorized: false,
		});

		let axiosOptions: AxiosRequestConfig = {
			httpsAgent: agent,
			headers: {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
				Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
				"Accept-Language": "en-US,en;q=0.5",
				"Accept-Encoding": "gzip, deflate, br",
				Connection: "keep-alive",
				"Upgrade-Insecure-Requests": "1",
				"Sec-Fetch-Dest": "document",
				"Sec-Fetch-Mode": "navigate",
				"Sec-Fetch-Site": "none",
				"Sec-Fetch-User": "?1",
				TE: "trailers",
			},
		};

		this.axios = axios.create(axiosOptions);
	}

	private ParseResponse(text: string) {
		let resData = {
			r: "",
			c: "",
			rc: "",
			responses: [],
			urls: new Set()
		};
		let parseData = (data: string) => {
			if (typeof data === "string") {
				if (data?.startsWith("c_")) {
					resData.c = data;
					return;
				}
				if (data?.startsWith("r_")) {
					resData.r = data;
					return;
				}
				if (data?.startsWith("rc_")) {
					resData.rc = data;
					return;
				}
				resData.responses.push(data);
			}
			if (Array.isArray(data)) {
				if (data.length == 5 && Number.isInteger(data[0]) && Array.isArray(data[2])) {
					if (data[2][0]) {
						resData.urls.add(data[2][0]);
					}
				}
				else {
					data.forEach((item) => {
						parseData(item);
					});
				}
			}
		};
		try {
			const lines = text.split("\n");
			for (let i in lines) {
				const line = lines[i];
				if (line.includes("wrb.fr")) {
					let data = JSON.parse(line);
					let responsesData = JSON.parse(data[0][2]);
					responsesData.forEach((response) => {
						parseData(response);
					});
				}
			}
		} catch (e: any) {
			console.log(e.message);
		}

		return resData;
	}

	private async GetRequestParams() {
		try {
			const response = await this.axios.get("https://bard.google.com", {
				headers: {
					Cookie: this.cookies,
				},
			});
			let $ = load(response.data);
			let script = $("script[data-id=_gd]").html();
			script = script.replace("window.WIZ_global_data", "googleData");
			const context = { googleData: { cfb2h: "", SNlM0e: "" } };
			vm.createContext(context);
			vm.runInContext(script, context);
			const at = context.googleData.SNlM0e;
			const bl = context.googleData.cfb2h;
			return { at, bl };
		} catch (e: any) {
			console.log(e.message);
		}
	}

	public async ask(prompt: string) {
		let resData = await this.send(prompt);
		return resData;
	}

	private async send(prompt: string) {
		try {
			let { at, bl } = await this.GetRequestParams();
			const response = await this.axios.post(
				"https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
				new URLSearchParams({
					at: at,
					"f.req": JSON.stringify([null, `[[${JSON.stringify(prompt)}],null,${JSON.stringify(["", "", ""])}]`]),
				}),
				{
					headers: {
						Cookie: this.cookies,
					},
					params: {
						bl: bl,
						rt: "c",
						_reqid: "0",
					},
				},
			);

			let parsedResponse = this.ParseResponse(response.data);

			return { response: parsedResponse.responses[0], sources: Array.from(parsedResponse.urls) };
		} catch (e: any) {
			console.log(e.message);
		}
	}
}

export default { Bard };
export { Bard };