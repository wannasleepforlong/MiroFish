/**
 * Temporarily stores the files and prompt before upload.
 * The home page redirects immediately and the Process page performs the API call.
 */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  simulationRequirement: '',
  enableNews: false,
  isPending: false
})

export function setPendingUpload(files, requirement, enableNews = false) {
  console.log('pendingUpload.js: setPendingUpload called with enableNews:', enableNews)
  state.files = files
  state.simulationRequirement = requirement
  state.enableNews = enableNews
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    enableNews: state.enableNews,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.simulationRequirement = ''
  state.enableNews = false
  state.isPending = false
}

export default state
