((w) => {
    w.onload = () => {
        const POST_FORM_CONTAINER = document.querySelector('.edit-post-form')

        if(POST_FORM_CONTAINER) {
            const TAGS_DATALIST = document.querySelector('#tags-datalist')
            const TAGS_INPUT = document.querySelector('#tags-input')
            const TAGS_CONTENT = document.querySelector('.tags-content')
            const POST_ID = POST_FORM_CONTAINER.dataset.postId
            const DOMAIN = w.location.origin
            const TAGS_PATH = '/posts/tags'
            const CREATE_TAG_PATH = '/posts/tags/create'
            const POST_TAGS_PATH = (id) => `/posts/${id}/get_tags`
            const ADD_POST_TAG_PATH = (id) => `/posts/${id}/set_tag`
            const REMOVE_POST_TAG_PATH = (id) => `/posts/${id}/remove_tag`
            let tags = []
            let postTags = []

            function createOption(value) {
                let option = document.createElement('option')
                option.value = value
                return option
            }

            function createLabel(item) {
                let label = document.createElement('span')
                let button = document.createElement('button')
                button.innerText = 'x'
                label.innerText = item.name
                label.dataset.tagId = item.id
                label.classList.add('tag-item')
                label.appendChild(button)
                return label
            }

            async function setInputEvent(input) {
                let process = async event => {
                    if(event.keyCode === 13) {
                        let tag = tags.find(item => item.name === event.target.value)
                        console.log('post tags: ', postTags)
                        if(!tag) {
                            let result = await createTag(event.target.value)
                            console.log('tag not exist')
                            console.log('result here: ', result)
                            if(result.status === 'created') {
                                let second_result = await setTagToPost(POST_ID, event.target.value)
                                if(second_result.status !== 'error') {
                                    postTags.push(result.data)
                                }
                                input.value = ""
                                tags.push(result.data)
                                await setPostTags(TAGS_CONTENT)
                                await setTagsForDataList(TAGS_DATALIST)
                                await setLabelEvent(TAGS_CONTENT)
                            }
                        } else {
                            let postTag = postTags.find(item => item.name === event.target.value)
                            if(!postTag) {
                                let result = await setTagToPost(POST_ID, event.target.value)
                                if(result.status !== 'error') {
                                    input.value = ""
                                    postTags.push(result.data)
                                    await setPostTags(TAGS_CONTENT)
                                    await setTagsForDataList(TAGS_DATALIST)
                                    await setLabelEvent(TAGS_CONTENT)
                                }
                            } else {
                                console.log('post has tag')
                            }
                        }
                    }
                }
                input.addEventListener('keyup', process)
            }

            async function createTag(name) {
                let body = new FormData()
                body.append('name', name)
                let uri = `${DOMAIN}${CREATE_TAG_PATH}`
                let result = await fetch(uri, {
                    method: 'post',
                    body
                })
                result = await result.json()
                return result
            }

            async function setTagToPost(id, tagName) {
                let body = new FormData()
                let method = 'post'
                body.append('name', tagName)
                let uri = `${DOMAIN}${ADD_POST_TAG_PATH(id)}`
                let request = await fetch(uri, {method, body})
                let response = await request.json()
                return response
            }

            async function getTags(domain, path) {
                let uri = `${domain}${path}`
                let tags = await fetch(uri, {method: 'get'})
                tags = await tags.json()
                return tags
            }

            async function setTagsForDataList(dataList) {
                dataList.innerHTML = ""
                let dataListTags = []
                tags.map(tag => {
                    let result = postTags.find(postTag => postTag.id == tag.id)
                    if (!result) {
                        dataListTags.push(tag)
                    }
                })
                dataListTags.map(tag => dataList.appendChild(createOption(tag.name)))
            }

            async function setPostTags(element) {
                element.innerHTML = ''
                postTags.map(tag => element.appendChild(createLabel(tag)))
            }

            async function labelEvent(event) {
                let {target} = event
                let body = new FormData()
                let method = 'post'
                let parent = target.parentElement
                console.log(target)
                console.log(parent)
                let {tagsElement} = target
                let uri = `${DOMAIN}${REMOVE_POST_TAG_PATH(POST_ID)}`
                let tagToDelete = String(parent.textContent)
                tagToDelete = tagToDelete.slice(0, tagToDelete.length - 1)
                body.append('name', tagToDelete)
                let request = await fetch(uri, {method, body})
                let response = await request.json()
                if(response.status === 'removed') {
                    postTags = postTags.filter(tag => tag.id !== response.data.id)
                    await setPostTags(tagsElement)
                    await setLabelEvent(tagsElement)
                } else {
                    console.log(response)
                }
            }

            async function setLabelEvent(element) {
                let buttons = document.querySelectorAll('.tag-item button')
                buttons.forEach(button => button.removeEventListener('click', labelEvent))
                //console.log(postTags)
                buttons.forEach(button => {
                    button.postTags = postTags
                    button.tagsElement = element
                    button.addEventListener('click', labelEvent)
                })
            }

            async function main() {
                let requestTags = await getTags(DOMAIN, TAGS_PATH)
                let requestPostTags = await getTags(DOMAIN, POST_TAGS_PATH(POST_ID))
                tags = requestTags.data
                postTags = requestPostTags.data
                await setPostTags(TAGS_CONTENT)
                await setTagsForDataList(TAGS_DATALIST)
                await setInputEvent(TAGS_INPUT)
                await setLabelEvent(TAGS_CONTENT)
            }

            main()
        }
    }
})(window)