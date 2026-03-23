import { reactive } from 'vue'

export const globalState = reactive({
  selectedCountries: [],
  tickerNews: []
})

export function setSelectedCountries(countries) {
  globalState.selectedCountries = countries
}

export function setTickerNews(news) {
  globalState.tickerNews = news
}
